<template>
  <v-dialog v-model="dialog" persistent max-width="700px" @keydown.esc="closeForm">
    <template #activator="{ props }">
      <slot name="activator" v-bind="{ props }">
        <v-btn v-bind="props"> New </v-btn>
      </slot>
    </template>
    <v-card>
      <v-form ref="form" lazy-validation @submit.prevent="submitForm">
        <v-card-title>
          {{ title }}
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="workspace.name"
                  autofocus
                  label="Workspace Name"
                  required
                  :rules="[(v: unknown) => !!v || 'This field is required']"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="workspace.data_specification.file_type"
                  :items="fileTypes"
                  label="File Type (optional)"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-menu
                  v-model="menuFrom"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="auto"
                >
                  <template #activator="{ props }">
                    <v-text-field
                      v-bind="props"
                      v-model="workspace.data_specification.date_from"
                      label="Date From (optional)"
                      readonly
                      clearable
                    />
                  </template>
                  <v-date-picker
                    v-model="workspace.data_specification.date_from"
                    @input="menuFrom = false"
                  />
                </v-menu>
              </v-col>
              <v-col cols="12" sm="6">
                <v-menu
                  v-model="menuTo"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="auto"
                >
                  <template #activator="{ props }">
                    <v-text-field
                      v-bind="props"
                      v-model="workspace.data_specification.date_to"
                      label="Date To (optional)"
                      readonly
                      clearable
                    />
                  </template>
                  <v-date-picker
                    v-model="workspace.data_specification.date_to"
                    @input="menuTo = false"
                  />
                </v-menu>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" type="button" @click="closeForm">Close</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="text"
            type="submit"
            :disabled="submitDisabled"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { type ComponentInstance, ref, watch } from 'vue';
import type { WorkspaceOut, WorkspaceIn, WorkspaceUpdate } from '@/api/resources/Workspace.ts';
import type { VForm } from 'vuetify/components';
import { useApi } from '@/api';
import { useReportingStore } from '@/stores/Reporting.ts';
import { pick } from 'lodash';


const workspaceProps = withDefaults(
  defineProps<{
    title?: string;
    editedWorkspace?: WorkspaceOut;
  }>(),
  {title: 'New workspace', editedWorkspace: undefined },
);

const emit = defineEmits<{
  (e: 'workspace-saved'): void;
}>();

defineSlots<{
  activator(props: { props: Record<string, any> }): any;
}>();

const workspace = ref<Partial<WorkspaceIn & WorkspaceUpdate>>({
  name: '',
  data_specification: {
    file_type: null,
    date_from: null,
    date_to: null,
  },
});

const dialog = ref(false);

const form = ref<ComponentInstance<typeof VForm>>();

function closeForm() {
  dialog.value = false;
}

const api = useApi();
const reportingStore = useReportingStore();

const submitDisabled = ref(false);
const menuFrom = ref(false);
const menuTo = ref(false);

const fileTypes = ['PDF', 'IMAGE'];

async function submitForm() {
  if (!form.value) return;

  const result = await form.value.validate();
  if (!result.valid) return;

  try {
    submitDisabled.value = true;
    if (workspaceProps.editedWorkspace?.id != null) {
      await api.workspace.update(
        workspaceProps.editedWorkspace.id,
        pick(workspace.value, ['name', 'data_specification']) as WorkspaceUpdate,
      );
    } else {
      await api.workspace.create(
        workspace.value as WorkspaceIn,
      );
    }
    workspace.value = { name: '', data_specification: { file_type: null, date_from: null, date_to: null } };
    emit('workspace-saved');
    closeForm();
  } catch (error) {
    console.error(error);
    reportingStore.reportError('Failed to save workspace.');
  } finally {
    submitDisabled.value = false;
  }
}

watch(
  () => workspaceProps.editedWorkspace,
  (newWs) => {
    if (newWs) {
      workspace.value = { ...newWs, data_specification: { ...newWs.data_specification } };
    }
  },
  { immediate: true },
);

</script>
