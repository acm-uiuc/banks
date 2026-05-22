export interface ISiteConfig {
  // Required
  title: string;
  description: string;
  image: string;
  timezone: string;
  // Optional
  twitterUsername?: string;
  color?: string;
  navLinks?: { name: string, url: string }[];
  socialLinks?: { name: string, url: string }[];
  // Masthead metadata for the current issue. Update this when rolling a new
  // issue in (see the rollover steps in README).
  currentIssue?: {
    volume: number;
    number: number;
    date: string;   // ISO date, e.g. "2025-10-31"
    title?: string; // optional issue theme/title
  };
  [key: string]: any;
};

const siteConfig: ISiteConfig = {
  title: "Banks of the Boneyard",
  description: "The Journal of the Association for Computing Machinery at UIUC",
  // image: "/assets/acm-blue-512x512.png",
  image: "https://static.acm.illinois.edu/square-blue.png",
  timezone: "America/Chicago",
  twitterUsername: "@acmuiuc",
  color: "#0053b3",
  currentIssue: {
    volume: 43,
    number: 1,
    date: "2025-10-31",
  },
};

export default siteConfig;