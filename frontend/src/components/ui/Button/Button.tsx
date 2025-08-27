import React from "react";
import { LucideIcon } from "lucide-react";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | "primary"
    | "secondary"
    | "outline"
    | "ghost"
    | "sidebar"
    | "navbar";
  size?: "sm" | "md" | "lg" | "xl";
  loading?: boolean;
  icon?: LucideIcon;
  iconPosition?: "left" | "right";
  children?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className = "",
      variant = "primary",
      size = "md",
      loading = false,
      disabled = false,
      icon: Icon,
      iconPosition = "left",
      children,
      type = "button",
      ...props
    },
    ref
  ) => {
    // Clases base usando CSS variables
    const baseClasses =
      "inline-flex items-center justify-center font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200 disabled:cursor-not-allowed";

    // Clases de variante (usando nuestro sistema CSS)
    const variantClasses = {
      primary: "btn-primary",
      secondary: "btn-secondary",
      outline: "btn-outline",
      ghost: "btn-ghost",
      sidebar: "btn-sidebar",
      navbar: "btn-navbar",
    };

    // Clases de tamaño usando Tailwind
    const sizeClasses = {
      sm: "px-3 py-1.5 text-sm rounded-md gap-1.5",
      md: "px-4 py-2 text-sm rounded-lg gap-2",
      lg: "px-6 py-2.5 text-base rounded-lg gap-2",
      xl: "px-8 py-3 text-lg rounded-xl gap-2.5",
    };

    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        type={type}
        className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
        disabled={isDisabled}
        {...props}
      >
        {loading && <div className="loading-spinner w-4 h-4" />}

        {!loading && Icon && iconPosition === "left" && (
          <Icon
            size={
              size === "sm" ? 14 : size === "lg" ? 18 : size === "xl" ? 20 : 16
            }
          />
        )}

        {children && <span>{children}</span>}

        {!loading && Icon && iconPosition === "right" && (
          <Icon
            size={
              size === "sm" ? 14 : size === "lg" ? 18 : size === "xl" ? 20 : 16
            }
          />
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button };
export default Button;
