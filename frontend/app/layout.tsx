import type { Metadata } from "next";
import { Bitter, Work_Sans, Fira_Code } from "next/font/google";
import "./globals.css";

/* Load three distinct fonts:
   - Bitter: slab serif for headings (warm, editorial feel)
   - Work Sans: geometric sans for body text
   - Fira Code: monospace for technical output */

const bitter = Bitter({
  variable: "--font-bitter",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const workSans = Work_Sans({
  variable: "--font-work-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

const firaCode = Fira_Code({
  variable: "--font-fira-code",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "HydraTask",
  description: "Turn vague tasks into actionable work packages",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${bitter.variable} ${workSans.variable} ${firaCode.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
