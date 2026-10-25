/** Loading indicator: the Crewloom mark weaving itself. Motion-sensitive viewers get the finished mark. */
export function LogoLoader({ label, size = 96 }: { label: string; size?: number }) {
  return (
    <span className="logo-loader" role="status" aria-label={label}>
      <picture>
        <source media="(prefers-reduced-motion: reduce)" srcSet="/logo.svg" />
        {/* eslint-disable-next-line @next/next/no-img-element -- animated SVG: next/image would serve it static */}
        <img src="/logo-loader.svg" width={size} height={size} alt="" draggable={false} />
      </picture>
    </span>
  );
}
