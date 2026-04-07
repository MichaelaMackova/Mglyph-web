import { mglyphClient } from '@/clients/mglyph_client'
import { authStore } from '@/main'
import type { AxiosResponse } from 'axios'
import type { UUID } from 'crypto'
import JSZip from 'jszip'

async function fetchZipFileAsArrayBuffer(fileId: UUID): Promise<AxiosResponse<ArrayBuffer>> {
  return await mglyphClient.get(`/file/${fileId}`, {
    authorizeEndpoint: authStore.user ? true : false,
    responseType: 'arraybuffer',
  })
}

type MetadataContent = {
  name: string
  short_name: string
  author: string
  images: [string, number][]
  version: string
}

type ZipFileContent = {
  metadata: MetadataContent | null
  images: { blobUrl: string; glyphValue: number }[]
}

async function unzip(zipFileBuffer: ArrayBuffer): Promise<ZipFileContent> {
  const zip = new JSZip()
  const zipFileContent = await zip.loadAsync(zipFileBuffer)

  const zipContent: ZipFileContent = {
    metadata: null,
    images: [],
  }

  var imageInfos: { blobUrl: string; relativePath: string }[] = []

  for (const [relativePath, fileEntry] of Object.entries(zipFileContent.files)) {
    // only files
    if (!fileEntry.dir) {
      // read metadata
      if (relativePath === 'metadata.json') {
        // load as blob
        const fileBlob = await fileEntry.async('blob')

        const reader = new FileReader()
        reader.readAsText(fileBlob)

        reader.onload = () => {
          zipContent.metadata = JSON.parse(reader.result as string)
          if (zipContent.metadata === null || zipContent.metadata === undefined) {
            throw new Error('Metadata is null or undefined')
          }
        }
      } else if (
        relativePath.endsWith('.png') ||
        relativePath.endsWith('.jpg') ||
        relativePath.endsWith('.jpeg')
      ) {
        // load as blob
        const fileBlob = await fileEntry.async('blob')

        const reader = new FileReader()
        reader.readAsDataURL(fileBlob)

        reader.onload = () => {
          imageInfos.push({
            blobUrl: reader.result as string,
            relativePath,
          })
        }
      }
    }
  }

  // map image Blobs to glyph values using metadata
  zipContent.images = imageInfos.map((imageInfo) => {
    const glyphValue = zipContent.metadata?.images.find(
      (glyphInfo) => glyphInfo[0] === imageInfo.relativePath,
    )?.[1]

    if (glyphValue === undefined) {
      throw new Error(`Glyph value not found for image: ${imageInfo.relativePath}`)
    }

    return {
      blobUrl: imageInfo.blobUrl,
      glyphValue,
    }
  })

  zipContent.images.sort((a, b) => a.glyphValue - b.glyphValue)

  return zipContent
}

export { fetchZipFileAsArrayBuffer, unzip, type ZipFileContent }
