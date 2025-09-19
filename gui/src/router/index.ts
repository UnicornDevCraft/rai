import { createRouter, createWebHistory } from 'vue-router';
import DocumentTemplateList from '@/views/DocumentTemplateList.vue';
import WorkspacesPage from '@/views/WorkspaceList.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/document-template',
      name: 'DocumentTemplateList',
      component: DocumentTemplateList,
    },
    {
      path: '/workspaces',
      component: WorkspacesPage
    },
  ],
});

export default router;
