import Link from "next/link";
import { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "md" | "lg";

type BaseProps = {
  children: ReactNode;
  className?: string;
  href?: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
};

type ButtonProps = BaseProps & ButtonHTMLAttributes<HTMLButtonElement>;

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "border border-transparent bg-[var(--accent)] !text-[var(--accent-contrast)] shadow-[var(--shadow-soft)] hover:opacity-92 hover:!text-[var(--accent-contrast)]",
  secondary:
    "border border-[var(--border)] bg-[var(--panel-strong)] text-[var(--foreground)] shadow-[var(--shadow-soft)] hover:bg-[var(--panel)]",
  ghost: "border border-transparent bg-transparent text-[var(--foreground-soft)] hover:bg-[var(--panel-subtle)] hover:text-[var(--foreground)]",
};

const sizeClasses: Record<ButtonSize, string> = {
  md: "h-10 px-4 text-sm",
  lg: "h-11 px-5 text-sm sm:text-base",
};

export function Button({
  children,
  className,
  href,
  size = "md",
  type = "button",
  variant = "primary",
  ...props
}: ButtonProps) {
  const classes = cn(
    "inline-flex cursor-pointer items-center justify-center rounded-full font-medium transition-colors duration-200 ease-out focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-60 motion-reduce:transition-none",
    variantClasses[variant],
    sizeClasses[size],
    className,
  );

  if (href) {
    return (
      <Link className={classes} href={href}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} type={type} {...props}>
      {children}
    </button>
  );
}
