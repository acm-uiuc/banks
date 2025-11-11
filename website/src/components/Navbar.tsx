import { AcmBannerLogo } from "@/components/AcmLogo";
import { BanksVerticalLogo } from "@/components/BanksLogo";

export default function Navbar() {
  return (
    <div className="flex flex-col gap-4 my-4 container">
      <div className="flex flex-row gap-4 w-full self-center">
        <span className="w-1/4 self-center">
          <a
            href="https://www.acm.illinois.edu/"
            target="blank"
            className="text-[#0053b3]"
          >
            <AcmBannerLogo className="max-w-fit h-16 md:h-24" />
          </a>
        </span>
        <span className="w-1/2 max-h-32">
          <a href="/">
            <BanksVerticalLogo />
          </a>
        </span>
        <span className="w-1/4" />
      </div>
      <nav className="flex flex-row gap-4 md:gap-6 lg:gap-8 self-center font-bold">
        <a href="/issues/latest">Latest Issue</a>
        <a href="/issues">All Issues</a>
        {/* <a href="/articles">All Articles</a> */}
        <a href="/articles?tag=sig-updates">SIG Updates</a>
        <a href="/articles?tag=deep-dives">Deep Dives</a>
        <a href="/articles?tag=life">Campus + Life</a>
        <a href="/articles?tag=fun">Fun</a>
        <a href="/about">About</a>
      </nav>
      <span className="w-full">
        <hr className="mb-1" />
        <hr />
      </span>
    </div>
  )
}