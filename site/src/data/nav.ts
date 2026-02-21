export type NavLink = {
  label: string;
  path: string;
  summary: string;
};

export type NavSection = {
  label: string;
  links: NavLink[];
};

export const NAV_SECTIONS: NavSection[] = [
  {
    label: 'Start',
    links: [
      { label: 'Home', path: '/', summary: 'Overview and direct links.' },
      { label: 'Start', path: '/start', summary: 'Install and run the first program.' },
      { label: 'CLI', path: '/cli', summary: 'All command flags and output modes.' },
      { label: 'Pipeline', path: '/pipeline', summary: 'Stage by stage compiler flow.' },
    ],
  },
  {
    label: 'Language',
    links: [
      { label: 'Language', path: '/language', summary: 'Types, expressions, flow, and memory.' },
      { label: 'Examples', path: '/examples', summary: 'All 36 examples with purpose.' },
      { label: 'Topics', path: '/topics', summary: 'Inline examples grouped by topic.' },
    ],
  },
  {
    label: 'Project',
    links: [
      { label: 'Status', path: '/status', summary: 'Coverage, tests, and deferred work.' },
      { label: 'Changelog', path: '/changelog', summary: 'Release level change history.' },
      { label: 'Visuals', path: '/visuals', summary: 'Large visual references.' },
    ],
  },
];
