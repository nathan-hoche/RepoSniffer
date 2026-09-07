import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://nathan-hoche.github.io/RepoSniffer/",
  base: "/RepoSniffer/",
  integrations: [
    starlight({
      title: "RepoSniffer",
      logo: {
        src: "./src/assets/icon.png",
      },
      customCss: ["./src/styles/custom.css"],
      head: [
        { tag: "meta", attrs: { property: "og:image", content: "https://nathan-hoche.github.io/RepoSniffer/og.png" } },
        { tag: "meta", attrs: { property: "og:image:width", content: "1280" } },
        { tag: "meta", attrs: { property: "og:image:height", content: "640" } },
        { tag: "meta", attrs: { name: "twitter:card", content: "summary_large_image" } },
        { tag: "meta", attrs: { name: "twitter:image", content: "https://nathan-hoche.github.io/RepoSniffer/og.png" } },
      ],
      social: {
        github: "https://github.com/nathan-hoche/RepoSniffer",
      },
      sidebar: [
        {
          label: "Start here",
          items: [
            { label: "Home", link: "/" },
            { label: "Getting started", link: "/getting-started/" },
            { label: "Using with agents", link: "/agents/" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "CLI reference", link: "/cli/" },
            { label: "Python API", link: "/api/" },
          ],
        },
        {
          label: "Under the hood",
          items: [
            { label: "Architecture", link: "/architecture/" },
            { label: "Evaluation", link: "/eval/" },
          ],
        },
        {
          label: "Project",
          items: [
            { label: "Contributing", link: "/contributing/" },
            { label: "Changelog", link: "/changelog/" },
          ],
        },
      ],
    }),
  ],
});