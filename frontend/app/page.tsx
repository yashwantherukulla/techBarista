import { title, subtitle } from '@/components/primitives';

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-20 md:mt-[8rem]">
      <div className="inline-block text-center justify-center">
        <h1 className={title()}>Make Coding Easier&nbsp;</h1>
        <br />
        <h1 className={title({ color: 'violet' })}>Regardless of your Experience.</h1>
        <h2 className={subtitle({ class: 'mt-8' })}>Crafting a tech stack roadmap, initiating from scratch, and navigating uncharted Git repositories.</h2>
        <h2 className={subtitle()}>We got you covered</h2>
      </div>
    </section>
  );
}
