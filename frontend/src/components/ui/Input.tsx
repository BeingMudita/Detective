import { forwardRef, useId } from "react";
import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, id, ...props }, ref) => {
    const autoId = useId();
    const inputId = id ?? autoId;
    return (
      <div>
        <label htmlFor={inputId} className="field-label">
          {label}
        </label>
        <input id={inputId} ref={ref} className="input" {...props} />
        {hint && <p className="mt-1 text-xs text-faint">{hint}</p>}
      </div>
    );
  },
);

Input.displayName = "Input";
