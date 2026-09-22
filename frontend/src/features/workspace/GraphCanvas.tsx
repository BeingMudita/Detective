import {
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useEffect } from "react";
import type { EdgeView, EntityView } from "../../lib/types";
import { EntityNode, type EntityNodeData } from "./EntityNode";

const nodeTypes = { entity: EntityNode };

function layoutPosition(index: number) {
  const perRing = 6;
  const ring = Math.floor(index / perRing);
  const angle = (index % perRing) * ((2 * Math.PI) / perRing) + ring * 0.5;
  const radius = 150 + ring * 140;
  return { x: 460 + radius * Math.cos(angle), y: 320 + radius * Math.sin(angle) };
}

interface Props {
  entities: EntityView[];
  edges: EdgeView[];
  interactive: boolean;
  onConnectEntities: (source: string, target: string) => void;
  onSelectEntity: (extId: string | null) => void;
}

export function GraphCanvas({
  entities,
  edges,
  interactive,
  onConnectEntities,
  onSelectEntity,
}: Props) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    setNodes((prev) => {
      const prevPos = new Map(prev.map((n) => [n.id, n.position]));
      return entities.map((e, i) => {
        const position = prevPos.get(e.ext_id) ?? layoutPosition(i);
        const data: EntityNodeData = { entity: e };
        return { id: e.ext_id, type: "entity", position, data } as Node;
      });
    });
  }, [entities, setNodes]);

  useEffect(() => {
    setRfEdges(
      edges.map(
        (e) =>
          ({
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.rel_type,
          }) as Edge,
      ),
    );
  }, [edges, setRfEdges]);

  const onConnect = useCallback(
    (conn: Connection) => {
      if (!interactive || !conn.source || !conn.target || conn.source === conn.target) return;
      setRfEdges((eds) => addEdge({ ...conn, id: `tmp-${conn.source}-${conn.target}` }, eds));
      onConnectEntities(conn.source, conn.target);
    },
    [interactive, onConnectEntities, setRfEdges],
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={rfEdges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      nodeTypes={nodeTypes}
      onNodeClick={(_, node) => onSelectEntity(node.id)}
      onPaneClick={() => onSelectEntity(null)}
      nodesConnectable={interactive}
      fitView
      minZoom={0.2}
      proOptions={{ hideAttribution: true }}
    >
      <Background variant={BackgroundVariant.Dots} gap={22} size={1} color="var(--border)" />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
