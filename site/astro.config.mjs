import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// The site deploys to GitHub Pages at https://nrynss.github.io/lambo-paper.
export default defineConfig({
  site: 'https://nrynss.github.io',
  base: '/lambo-paper',
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
  },
  integrations: [
    starlight({
      title: 'Lambo',
      description: 'A Living Topological Memory Substrate for Multi-Agent Software Development',
      favicon: '/favicon.svg',
      customCss: ['katex/dist/katex.min.css'],
      // Google Scholar and Dublin Core citation metadata for the web edition.
      head: [
        { tag: 'meta', attrs: { name: 'citation_title', content: 'Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development' } },
        { tag: 'meta', attrs: { name: 'citation_author', content: 'Narayan SS' } },
        { tag: 'meta', attrs: { name: 'citation_publication_date', content: '2026/09/08' } },
        { tag: 'meta', attrs: { name: 'citation_online_date', content: '2026/09/08' } },
        { tag: 'meta', attrs: { name: 'citation_pdf_url', content: 'https://nrynss.github.io/lambo-paper/lambo-paper.pdf' } },
        { tag: 'meta', attrs: { name: 'citation_abstract_html_url', content: 'https://nrynss.github.io/lambo-paper/' } },
        { tag: 'meta', attrs: { name: 'citation_technical_report_institution', content: 'Independent' } },
        { tag: 'meta', attrs: { name: 'DC.title', content: 'Lambo: A Living Topological Memory Substrate for Multi-Agent Software Development' } },
        { tag: 'meta', attrs: { name: 'DC.creator', content: 'Narayan SS' } },
        { tag: 'meta', attrs: { name: 'DC.date', content: '2026-09-08' } },
        { tag: 'meta', attrs: { name: 'DC.type', content: 'Text' } },
        { tag: 'meta', attrs: { name: 'DC.identifier', content: 'https://github.com/nrynss/lambo-paper' } },
      ],
      social: [
        { icon: 'github', label: 'Paper Repo', href: 'https://github.com/nrynss/lambo-paper' },
        { icon: 'external', label: 'Lambo Core', href: 'https://github.com/nrynss/lambo' },
      ],
      sidebar: [
        {
          label: 'Paper',
          items: [
            { label: '1. Introduction', slug: '01-introduction' },
            { label: '2. System Model & Topology', slug: '02-system-model' },
            { label: '3. 3-Phase Recall Engine', slug: '03-recall-engine' },
            { label: '4. Receipts & Write Queue', slug: '04-receipts-queue' },
            { label: '5. Empirical Evaluation', slug: '05-evaluation' },
            { label: '6. Related Work', slug: '06-related-work' },
            { label: '7. Limitations & Open Problems', slug: '07-limitations' },
            { label: '8. References', slug: '08-references' },
          ],
        },
        {
          label: 'Artifacts & Reproducibility',
          items: [
            { label: 'Download PDF', slug: 'download-pdf' },
            { label: 'Multi-Rig Telemetry', slug: 'telemetry-data' },
            { label: 'Replication Guide', slug: 'replication' },
          ],
        },
      ],
    }),
  ],
});
