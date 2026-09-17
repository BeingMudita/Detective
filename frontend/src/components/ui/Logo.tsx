interface LogoProps {
  size?: number;
  withWordmark?: boolean;
}

export function Logo({ size = 30, withWordmark = true }: LogoProps) {
  return (
    <div className="flex items-center gap-2.5">
      <span
        className="grid place-items-center rounded-lg bg-accent font-semibold text-bg"
        style={{ width: size, height: size, fontSize: size * 0.52 }}
        aria-hidden
      >
        🕵
      </span>
      {withWordmark && (
        <span className="text-[15px] font-semibold tracking-tight">
          Internet <span className="text-accent">Detective</span>
        </span>
      )}
    </div>
  );
}
