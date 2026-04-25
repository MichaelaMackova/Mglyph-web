<template>
  <div class="main-padding">
    <div v-if="isLoading" class="main-top-margin main-bottom-margin">
      Loading glyph data... <i class="fa-solid fa-spinner fa-spin-pulse"></i>
    </div>
    <div v-else-if="errorOccurred || !mglyphData" class="main-top-margin main-bottom-margin">
      <PopupNote
        message="An error occurred while fetching glyph data. Please try again later."
        type="error"
        :closable="false"
        width="max-content"
      />
    </div>
    <div v-else>
      <h1>{{ mglyphData.long_name }}</h1>
      <h2 class="author">by {{ mglyphData.author.username }}</h2>
      <div class="info-column">
        <div class="info-piece">
          <span class="label">Last updated:</span>
          {{ mglyphData.last_updated.toLocaleString() }}
        </div>
        <div class="info-piece">
          <span class="label">Short name:</span> {{ mglyphData.short_name }}
        </div>
        <div class="info-piece">
          <span class="label">Version:</span> {{ mglyphZipFile?.metadata?.version ?? 'unknown' }}
        </div>
      </div>
      <div class="info-column">
        <div class="info-piece">
          <span class="label">Submitted in challenge:</span>
          <RouterLink :to="{ name: 'ChallengeDetail', params: { id: mglyphData.challenge.id } }">{{
            mglyphData.challenge.title
          }}</RouterLink>
        </div>
        <div class="info-piece">
          <span class="label">Submitted:</span> {{ mglyphData.submission_time.toLocaleString() }}
        </div>
        <div class="info-piece">
          <span class="label">Score:</span>
          {{
            mglyphData.evaluation.score
              ? `${mglyphData.evaluation.score} (#${mglyphData.evaluation.rank})`
              : 'N/A'
          }}
        </div>
      </div>

      <div class="cards-container">
        <v-tabs v-model="currentTab" color="primary">
          <v-tab value="static"
            ><div class="icon-wrapper"><MGlyphStaticIcon /></div>
            Static</v-tab
          >
          <v-tab value="dynamic"
            ><div class="icon-wrapper"><MGlyphDynamicIcon /></div>
            Dynamic</v-tab
          >
          <v-tab value="code"
            ><div class="icon-wrapper"><i class="fa-solid fa-code"></i></div>
            Code</v-tab
          >
        </v-tabs>

        <v-divider></v-divider>

        <v-tabs-window v-model="currentTab" class="main-bottom-margin">
          <v-tabs-window-item value="static">
            <div class="card-content-container">
              <div v-if="errorOccurredZip || (!mglyphZipFile && !isLoadingZip)">
                <PopupNote
                  message="An error occurred while fetching the glyph's images. Please try again later."
                  type="error"
                  :closable="false"
                  width="max-content"
                />
              </div>
              <div v-else>
                <MGlyphStaticTab :zipFileContent="mglyphZipFile" :isLoadingZip="isLoadingZip" />
              </div>
            </div>
          </v-tabs-window-item>
          <v-tabs-window-item value="dynamic">
            <div class="card-content-container">
              <div v-if="errorOccurredZip || (!mglyphZipFile && !isLoadingZip)">
                <PopupNote
                  message="An error occurred while fetching the glyph's images. Please try again later."
                  type="error"
                  :closable="false"
                  width="max-content"
                />
              </div>
              <div v-else>
                <MGlyphDynamicTab :zipFileContent="mglyphZipFile" :isLoadingZip="isLoadingZip" />
              </div>
            </div>
          </v-tabs-window-item>
          <v-tabs-window-item value="code">
            <div class="card-content-container">
              <div v-if="mglyphData.is_code_public && mglyphData.code" class="code">
                {{ mglyphData.code }}
              </div>
              <div v-else>
                <PopupNote
                  message="The code for this malleable glyph is not available."
                  type="info"
                  :closable="false"
                  width="max-content"
                />
              </div>
            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PopupNote from '@/components/PopupNote.vue'
import MGlyphStaticIcon from '@/components/icons/MGlyphStaticIcon.vue'
import MGlyphDynamicIcon from '@/components/icons/MGlyphDynamicIcon.vue'
import MGlyphStaticTab from '@/components/MGlyphStaticTab.vue'
import MGlyphDynamicTab from '@/components/MGlyphDynamicTab.vue'
import { mglyphClient } from '@/clients/mglyph_client'
import { MGlyphDetail } from '@/services/types'
import { fetchZipFileAsArrayBuffer, unzip, type ZipFileContent } from '@/services/zip-file-utils'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
const router = useRouter()

const currentTab = ref<'static' | 'dynamic' | 'code'>('static')
const isLoading = ref<boolean>(true)
const errorOccurred = ref<boolean>(false)
const isLoadingZip = ref<boolean>(true)
const errorOccurredZip = ref<boolean>(false)

const mglyphData = ref<MGlyphDetail | null>(null)
const mglyphZipFile = ref<ZipFileContent | null>(null)

async function fetchGlyphData() {
  isLoading.value = true
  errorOccurred.value = false
  isLoadingZip.value = true
  errorOccurredZip.value = false
  try {
    const response = await mglyphClient.get(`/mglyph/${router.currentRoute.value.params.id}`, {
      authorizeEndpoint: false,
    })
    mglyphData.value = MGlyphDetail.fromAPIResponse(response.data)

    try {
      const zipResponse = await fetchZipFileAsArrayBuffer(mglyphData.value.file_id)
      mglyphZipFile.value = await unzip(zipResponse.data)
    } catch (zipError) {
      console.error('Error fetching or unzipping glyph zip file:', zipError)
      errorOccurredZip.value = true
    }
  } catch (error) {
    console.error('Error fetching glyph data:', error)
    errorOccurred.value = true
    errorOccurredZip.value = true
  } finally {
    isLoading.value = false
    isLoadingZip.value = false
  }
}

fetchGlyphData()
</script>

<style lang="css" scoped>
.author {
  margin-left: 1em;
  margin-top: -0.5em;
}

.info-column {
  display: inline-block;
  vertical-align: top;
  margin-right: 40px;
  width: calc(50% - 40px);
}

.info-piece {
  margin: 6px 0;

  .label {
    font-weight: bold;
    margin-right: 4px;
  }
}

.cards-container {
  margin: 20px 40px 0 40px;
  background: rgba(124, 124, 124, 0.16);
  box-shadow: 2px 2px 5px 0 rgba(128, 128, 128, 0.5);
  --v-theme-primary: var(--md-sys-color-primary, 240, 113, 103);
}

.card-content-container {
  padding: 20px;
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
}

.glyph-small-image {
  width: 100px;
  aspect-ratio: 1/1;
}

.code {
  font-family: 'Courier New', Courier, monospace;
}

.v-tab {
  font-weight: bold;
}
</style>
