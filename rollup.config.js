import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import html, { makeHtmlAttributes } from '@rollup/plugin-html';
import commonjs from '@rollup/plugin-commonjs';

const template = async ({attributes, files, meta, publicPath, title}) => {
  const scripts = (files.js || [])
    .map(({ fileName }) => {
      const attrs = makeHtmlAttributes(attributes.script);
      return `<script src="${publicPath}${fileName}"${attrs}></script>`;
    })
    .join('\n');

  const links = (files.css || [])
    .map(({ fileName }) => {
      const attrs = makeHtmlAttributes(attributes.link);
      return `<link href="${publicPath}${fileName}" rel="stylesheet"${attrs}>`;
    })
    .join('\n');

  const metas = meta
    .map((input) => {
      const attrs = makeHtmlAttributes(input);
      return `<meta${attrs}>`;
    })
    .join('\n');

  return `
<!doctype html>
<html${makeHtmlAttributes(attributes.html)}>
  <head>
    ${metas}
    <title>${title}</title>
    ${links}
  </head>
  <body>
    ${scripts}
    <app-main></app-main>
  </body>
</html>`;
};

export default {
  input: 'src/index.ts',
  output: {
    dir: 'output',
    format: 'iife',
  },
  plugins: [commonjs(), typescript(), resolve(), html({title: "Microfrontend Demo", template, publicPath: "/static/"})]
};
