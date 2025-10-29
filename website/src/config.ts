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
};

export default siteConfig;