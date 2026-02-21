// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://airbus5717.github.io',
	base: '/a7-py',
	integrations: [
		starlight({
			title: 'A7 Compiler Docs',
			description: 'Documentation for the A7 language and the a7-py compiler.',
			favicon: '/favicon.svg',
			customCss: ['./src/styles/docs.css'],
			pagefind: false,
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/airbus5717/a7-py',
				},
			],
			sidebar: [
				{
					label: 'Get Started',
					items: [
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quickstart', slug: 'getting-started/quickstart' },
					],
				},
				{
					label: 'Compiler Usage',
					items: [
						{ label: 'CLI Reference', slug: 'compiler/cli-reference' },
						{ label: 'Modes and Output', slug: 'compiler/modes-and-output' },
						{ label: 'Pipeline Overview', slug: 'compiler/pipeline-overview' },
					],
				},
				{
					label: 'Language Guide',
					items: [
						{ label: 'Types', slug: 'language/types' },
						{
							label: 'Declarations and Expressions',
							slug: 'language/declarations-and-expressions',
						},
						{ label: 'Control Flow', slug: 'language/control-flow' },
						{ label: 'Functions', slug: 'language/functions' },
						{ label: 'Generics', slug: 'language/generics' },
						{ label: 'Memory Management', slug: 'language/memory-management' },
						{ label: 'Modules and Visibility', slug: 'language/modules-and-visibility' },
						{ label: 'Builtins and Operators', slug: 'language/builtins-and-operators' },
						{ label: 'Grammar Summary', slug: 'language/grammar-summary' },
						{ label: 'Diagnostics and Limits', slug: 'language/diagnostics-and-limits' },
					],
				},
				{
					label: 'Examples',
					items: [
						{ label: 'Examples Index', slug: 'examples/examples-index' },
						{ label: 'By Topic', slug: 'examples/by-topic' },
					],
				},
				{
					label: 'Project Status',
					items: [
						{ label: 'Changelog', slug: 'project/changelog' },
						{ label: 'Missing Features', slug: 'project/missing-features' },
					],
				},
			],
		}),
	],
});
