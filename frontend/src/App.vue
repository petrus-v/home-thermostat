<template>
  <div id="app" class="container">
    <b-navbar class="main-nav-bar">
      <template slot="brand">
        <b-navbar-item tag="router-link" :to="{ name: 'home' }">
          <img src="@/assets/logo.png" alt="Thermostat" />
        </b-navbar-item>
      </template>
      <!--
      <template slot="start">
        <b-navbar-item tag="router-link" :to="{ name: 'new-direct-quotation' }">
          Devis
        </b-navbar-item>
        <b-navbar-dropdown label="Info">
          <b-navbar-item tag="router-link" :to="{ name: 'about' }">
            About
          </b-navbar-item>
        </b-navbar-dropdown>
      </template>
      -->
      <template slot="end">
        <h1 class="title">{{ $route.meta.title }}</h1>
      </template>
    </b-navbar>
    <router-view />
    <footer class="footer">
      <div class="content has-text-centered">
        <p>
          <strong>Home Theremostat</strong> par
        <a href="https://pierre.verkest.fr">Pierre Verkest</a>.
        </p>
      </div>
    </footer>
  </div>
</template>

<style>
.main-nav-bar {
  margin-bottom: 1em;
}
</style>
