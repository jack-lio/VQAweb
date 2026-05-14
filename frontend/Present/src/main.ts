import { createApp } from "vue";
import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import App from "./App.vue";
import Normal from "./pages/Normal.vue";
import "./global.css";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Normal",
    component: Normal,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((toRoute, _, next) => {
  const metaTitle = toRoute?.meta?.title as string;
  const metaDesc = toRoute?.meta?.description as string;

  window.document.title = metaTitle || "VQAweb";
  if (metaDesc) {
    addMetaTag(metaDesc);
  }
  next();
});

const addMetaTag = (value: string) => {
  const element = document.querySelector("meta[name='description']");
  if (element) {
    element.setAttribute("content", value);
  }
};

createApp(App).use(router).mount("#app");

export default router;
