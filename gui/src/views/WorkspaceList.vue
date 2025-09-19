<template>
  <v-container>
    <v-card>
      <v-card-title> Workspaces </v-card-title>
      <v-card-text>
        <v-data-table
          ref="workspaceTable"
          density="compact"
          :headers="headers"
          :loading="loadingInProgress"
          :items="workspaces"
          :search="search"
          item-value="id"
          multi-sort
          class="mt-10 px-10"
        >
          <template #top>
            <v-toolbar flat density="compact">
              <v-text-field
                v-model="search"
                prepend-icon="mdi-magnify"
                label="Search"
                class="ml-1"
                single-line
                hide-details
              />
              <v-spacer />
              <workspace-form
                dialog-title="New Workspace"
                @workspace-saved="fetchWorkspaces"
              />
            </v-toolbar>
          </template>
          <template #item.data_spec="{ item }">
            <div>
                <div v-if="item.data_specification.file_type">
                    File: {{ item.data_specification.file_type || '—' }}
                </div>
                <div v-if="item.data_specification.date_from">
                    From: {{ item.data_specification.date_from ? new Date(item.data_specification.date_from).toLocaleDateString() : '—' }}
                </div>
                <div v-if="item.data_specification.date_to">
                    To: {{ item.data_specification.date_to ? new Date(item.data_specification.date_to).toLocaleDateString() : '—' }}
                </div>
                <div v-if="!item.data_specification.file_type && !item.data_specification.date_from && !item.data_specification.date_to">
                None
                </div>
            </div>
          </template>
          <template #item.actions="{ item }">
            <div class="d-inline-block text-no-wrap">
              <workspace-form
                title="Update Workspace"
                :edited-template="item"
                @workspace-saved="fetchWorkspaces"
              >
                <template #activator="{ props }">
                  <v-btn
                    variant="plain"
                    class="pt-1"
                    icon="mdi-border-color"
                    v-bind="props"
                  />
                </template>
              </workspace-form>
              <v-btn
                variant="plain"
                color="red"
                icon="mdi-delete"
                @click="deleteWorkspace(item.id)"
              />
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import WorkspaceForm from '@/components/workspace/WorkspaceForm.vue';
import { type ComponentInstance, onMounted, ref } from 'vue';
import type { WorkspaceOut } from '@/api/resources/Workspace.ts';
import { useApi } from '@/api';
import { useReportingStore } from '@/stores/Reporting.ts';
import type { VDataTable } from 'vuetify/components';

const headers = [
  { title: 'Name', align: 'start', sortable: true, key: 'name' },
  { title: 'Data Specification', align: 'center', sortable: false, key: 'data_spec' },
  { title: 'Actions', align: 'end', sortable: false, key: 'actions' },
] as const;

const search = ref('');

const api = useApi();
const reportingStore = useReportingStore();

const loadingInProgress = ref(true);
const workspaces = ref<WorkspaceOut[]>([]);

const workspaceTable = ref<ComponentInstance<typeof VDataTable>>();

async function fetchWorkspaces() {
  try {
    loadingInProgress.value = true;
    workspaces.value = await api.workspace.list();
  } catch (e) {
    console.error(e);
    reportingStore.reportError('Failed to fetch workspaces');
  } finally {
    loadingInProgress.value = false;
  }
}

async function deleteWorkspace(workspaceId: number) {
  try {
    const confirmed = confirm('Are you sure?');
    if (!confirmed) return;

    await api.workspace.delete(workspaceId);
    await fetchWorkspaces();
  } catch (e) {
    console.error(e);
    reportingStore.reportError('Failed to delete workspace');
  }
}

onMounted(() => {
  fetchWorkspaces();
});
</script>