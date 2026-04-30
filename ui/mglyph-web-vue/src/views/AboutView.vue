<template>
  <div class="main-padding main-top-margin main-bottom-margin about-content">
    <h1 class="anchor" id="the-malleable-glyph-challenge">
      The Malleable Glyph Challenge<a
        class="headerlink"
        href="#the-malleable-glyph-challenge"
        title="Permanent link"
        ><i class="fa-solid fa-paragraph"></i
      ></a>
    </h1>
    <div class="section">
      <h2 class="anchor" id="what-is-a-malleable-glyph">
        What is a Malleable Glyph?<a
          class="headerlink"
          href="#what-is-a-malleable-glyph"
          title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <p>
          Malleable Glyph is a <strong>small graphical design</strong>, fitting exactly to a
          <strong>square of 1in&nbsp;&times;&nbsp;1in</strong>. It is
          <strong>"shaped" by a numerical parameter</strong> <em>x</em> ranging from <em>0.0</em> to
          <em>100.0</em>.
        </p>
        <p>
          For example, a very simple malleable glyph is a horizontal line that is extremely short
          for
          <em>x=0.0</em> and as long as possible for <em>x=100.0</em>:
        </p>
        <p>
          <img
            class="img-padding"
            alt="simple horizontal line"
            :src="simpleHorizontalLineImg"
            width="600"
          />
        </p>
        <p>
          Like every other graphical design, certain malleable glyph can be prettier or uglier. But
          there is another property of a malleably glyph that we are also interested in: its
          <strong>resolution</strong>, or how many different "sizes" of the glyph can be recognized
          by a naked human eye.
        </p>
        <p>
          For example, a scaled five-pointed star has a somewhat better resolution than the simple
          horizontal line.
        </p>
        <p>
          <img class="img-padding" alt="simple scaled star" :src="fivePointedStarImg" width="600" />
        </p>
      </div>
    </div>
    <div class="section">
      <h3 class="anchor" id="tutorial">
        The Tutorial<a class="headerlink" href="#tutorial" title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h3>
      <div class="section-content">
        <p>
          To learn working with the <span class="code">mglyph</span> library, it's best to start
          with
          <a
            href="https://colab.research.google.com/drive/1T8DHWpUBLNbo-QB5o6SXDjZrHjSVp4vv"
            target="_blank"
            >the tutorial:
            <img
              :src="tutorialScreenshotImg"
              alt="Tutorial Screenshot"
              width="100%"
              style="margin-top: 12px"
            />
          </a>
        </p>
        <p>
          In case something doesn't work as expected, something needs more clarification, or you
          have a suggestion for another functionality, please,
          <a href="https://www.fit.vut.cz/person/herout/" target="_blank">contact us</a>.
        </p>
      </div>
    </div>
    <div class="section">
      <h3 class="anchor" id="malleable-glyph-zoo">
        The Malleable Glyph Zoo<a
          class="headerlink"
          href="#malleable-glyph-zoo"
          title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h3>
      <div class="section-content">
        <p>
          There is a growing set of glyphs produced by various people -
          <a
            href="https://colab.research.google.com/drive/1hCSkbRpPCVYL4toh4p-YilIVe9rl3l98?hl=en#scrollTo=rnLV1d5J_mJe"
            target="_blank"
            >The Zoo of Malleable Glyphs</a
          >. You may find inspiration there.
        </p>
      </div>
    </div>
    <div class="section">
      <h2 class="anchor" id="what-is-the-malleable-glyph-challenge">
        What is The Malleable Glyph Challenge?<a
          class="headerlink"
          href="#what-is-the-malleable-glyph-challenge"
          title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <p>
          It is possible to <strong>objectively evaluate</strong> the resolution of a malleable
          glyph compared to other glyph designs. For example, the following four glyphs were
          evaluated by human subjects using our evaluation tool:
        </p>
        <p>
          <img class="img-padding" :src="fourGlyphsImg" alt="Four Glyphs" width="600" />
        </p>
        <p>
          <img
            class="img-padding"
            :src="fourGlyphsPlotImg"
            alt="Glyph Resolution Plotted"
            width="600"
          />
        </p>
        <p>
          The chart compares the resolution of the four glyphs. Higher curve is better than a lower
          curve.
        </p>
        <p>
          Malleable glyphs can differ in <strong>countless graphical aspects</strong>: shape, color,
          texture, complexity, fractal structure, use of the space, contrast, etc., etc. We are
          <strong>interested</strong> in what features make one malleable glyph design
          <strong>better than another</strong>. And we would love to see designs that
          <strong>so cleverly and so knowledgeably</strong> use the
          <em>1in&nbsp;&times;&nbsp;1in</em> space that they overcome other designs.
        </p>
        <p>
          We challenge anyone and everyone to design
          <strong>the best malleable glyph ever</strong>. We pledge to evaluate submitted malleable
          glyphs in a fair manner. We intend to periodically publish the top-performing malleable
          glyph designs and to analyze what factors seem to be strong and useful. We
          <strong>invite the designers of top-perforing and influential malleable glyphs</strong>
          to co-author the scientific publications and to join us in deepening the knowledge and
          understanding of human perception and graphical design.
        </p>
        <p>
          See a
          <a href="https://arxiv.org/abs/2503.16135" target="_blank"
            >detailed description of The Malleable Glyph Challenge in a published paper</a
          >.
        </p>
      </div>
    </div>
    <div class="section">
      <h2 class="anchor" id="use-the-self-evaluation-tool">
        Use the Self-Evaluation Tool<a
          class="headerlink"
          href="#use-the-self-evaluation-tool"
          title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <ol>
          <li>
            <p>Create one or more glyphs, export them to files.</p>
          </li>
          <li>
            <p>
              Put your exported glyphs into our
              <strong
                ><a href="https://tmgc.fit.vutbr.cz/self-eval/" target="_blank"
                  >Self-Evaluation Tool</a
                ></strong
              >.
            </p>
          </li>
          <li>
            <p>See for yourself how your glyphs are performing.</p>
          </li>
        </ol>
        <p>
          The Self-Evaluation Tool works entirely in your web browser. Glyphs that you insert into
          the tool are <strong>not uploaded</strong> anywhere, but they
          <strong>stay in your computer</strong>.
        </p>
      </div>
    </div>
    <div class="section">
      <h2 class="anchor" id="faq">
        FAQ<a class="headerlink" href="#faq" title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <p>Ask and we will answer.</p>
      </div>
    </div>
    <div class="section">
      <h2 class="anchor" id="research-articles">
        Research Articles<a class="headerlink" href="#research-articles" title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <p>
          Herout, A., Bartl, V., Gaens, M., & Tvrďoch, O. (2025). The Malleable Glyph (Challenge).
          Computing Research Repository (CoRR) in arXiv.
          <a href="https://doi.org/10.48550/arXiv.2503.16135" target="_blank"
            >https://doi.org/10.48550/arXiv.2503.16135</a
          >
        </p>
      </div>
    </div>
    <div class="section">
      <h2 class="anchor" id="contact">
        Contact<a class="headerlink" href="#contact" title="Permanent link"
          ><i class="fa-solid fa-paragraph"></i
        ></a>
      </h2>
      <div class="section-content">
        <p>We will be happy to hear from you.</p>
        <p>
          Please, e-mail
          <a href="https://www.fit.vut.cz/person/herout/" target="_blank">Adam Herout</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import simpleHorizontalLineImg from '@/assets/simple-horizontal-line.png'
import fivePointedStarImg from '@/assets/five-pointed-star.png'
import tutorialScreenshotImg from '@/assets/tutorial-screenshot.png'
import fourGlyphsImg from '@/assets/sample-glyphs.png'
import fourGlyphsPlotImg from '@/assets/sample-plot.png'
</script>

<style lang="css" scoped>
.about-content {
  max-width: 950px;
  margin-left: auto;
  margin-right: auto;
}

#the-malleable-glyph-challenge {
  text-align: center;
}

.anchor {
  scroll-margin-top: 100px;
}

a.headerlink {
  font-size: 0.7em;
  margin-left: 0.5rem;
  display: inline-block;
  vertical-align: middle;
  text-decoration: none;

  opacity: 0;
  color: rgba(var(--md-sys-color-on-surface, 32, 27, 19), 0.25);
  transition:
    color 0.25s,
    opacity 125ms;

  &:hover {
    color: rgb(var(--md-sys-color-secondary, 0, 175, 185));
  }
}

.anchor:hover a.headerlink {
  opacity: 1;
  transition:
    color 0.25s,
    opacity 125ms;
}

.section {
  margin-top: 2rem;
  margin-bottom: 2rem;

  .section-content {
    padding: 0 1rem;
  }
}

.img-padding {
  background-color: white;
  padding: 10px;
  border: 1px solid rgba(var(--md-sys-color-on-surface, 32, 27, 19), 0.25);
  border-radius: 16px;
}
</style>
