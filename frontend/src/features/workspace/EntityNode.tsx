import { Handle, Position, type NodeProps } from "@xyflow/react";
import { entityMeta } from "../../lib/presentation";
import type { EntityView } from "../../lib/types";

export interface EntityNodeData {
  entity: EntityView;
  [key: string]: unknown;
}

export function EntityNode({ data, selected }: NodeProps) {
  const { entity } = data as unknown as EntityNodeData;
  const meta = entityMeta(entity.type);
  return (
    <div
      className={`rounded-xl border bg-surface px-3 py-2 shadow-card ${
        selected ? "border-accent" : "border-border"
      }`}
      style={{ width: 184 }}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !border-0 !bg-accent-2" />
      <div className="flex items-center gap-2">
        <span className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-surface-2 text-sm">
          {meta.icon}
        </span>
        <div className="min-w-0">
          <div className="truncate font-mono text-[13px] text-text">{entity.label}</div>
          <div className="font-mono text-[9px] uppercase tracking-wider text-faint">
            {meta.label}
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !border-0 !bg-accent" />
    </div>
  );
}
