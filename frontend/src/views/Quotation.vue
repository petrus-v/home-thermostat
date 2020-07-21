<template>
  <div class="columns is-mobile" data-se="quotations-pages">
    <aside class="menu column is-one-quarter">
      <b-menu>
        <b-menu-list label="Menu">
          <b-menu-item
            icon="information-outline"
            label="Nouveau"
            tag="router-link"
            :to="{ name: 'new-direct-quotation' }"
          ></b-menu-item>
        </b-menu-list>
      </b-menu>
    </aside>
    <section class="column">
      <b-collapse>
        <b-collapse :open="false" aria-id="contentIdForA11y1">
          <b-button
            class="is-pulled-right"
            slot="trigger"
            aria-controls="contentIdForA11y1"
            icon-right="information-outline"
          ></b-button>
          <b-message type="is-info" has-icon>Some informations.</b-message>
        </b-collapse>
      </b-collapse>
      <router-view></router-view>
    </section>
  </div>
</template>
<style scoped>
aside {
  margin-left: 1em;
}
</style>
