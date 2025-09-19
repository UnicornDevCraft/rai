<template>
  <v-navigation-drawer
    theme="dark"
    permanent
    clipped
    :rail="minified"
    rail-width="70"
  >
    <v-list nav>
      <v-list-item
        title="Document templates"
        to="/document-template/"
        prepend-icon="mdi-card-account-details-outline"
      />
      <v-list-item
        title="Workspaces"
        to="/workspaces"
        prepend-icon="mdi-folder-outline"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
defineProps<{
  minified: boolean;
}>();
</script>
