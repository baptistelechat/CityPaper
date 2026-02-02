import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 p-8 font-sans sm:p-20">
      <main className="flex flex-col items-center gap-8 text-center">
        <h1 className="text-4xl font-bold tracking-tighter">CityPaper</h1>
        <p className="text-lg text-muted-foreground">
          Setup Complete: Next.js 15 + Tailwind 4 + shadcn/ui
        </p>

        <div className="flex gap-4">
          <Button variant="default">Default (Brutalist)</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="destructive">Destructive</Button>
        </div>
      </main>
    </div>
  );
}
