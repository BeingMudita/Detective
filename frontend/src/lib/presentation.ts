export interface EntityMeta {
  icon: string;
  label: string;
}

const ENTITY_META: Record<string, EntityMeta> = {
  username: { icon: "@", label: "Username" },
  email: { icon: "✉", label: "Email" },
  domain: { icon: "🌐", label: "Domain" },
  ip: { icon: "🖧", label: "IP Address" },
  person: { icon: "🧑", label: "Person" },
  file: { icon: "📄", label: "File" },
  social: { icon: "💬", label: "Social Profile" },
  image: { icon: "🖼", label: "Image" },
  device: { icon: "💻", label: "Device" },
  org: { icon: "🏢", label: "Organisation" },
};

export function entityMeta(type: string): EntityMeta {
  return ENTITY_META[type] ?? { icon: "◆", label: type };
}

export function reliabilityClass(reliability: string): string {
  switch (reliability) {
    case "high":
      return "text-good border-good";
    case "medium":
      return "text-warn border-warn";
    default:
      return "text-bad border-bad";
  }
}

export function toolLabel(tool: string): string {
  const map: Record<string, string> = {
    search: "Search",
    email: "Email Intel",
    domain: "DNS / Domain",
    ip: "IP Intel",
    identity: "Identity",
    image: "Image",
    file: "File Metadata",
  };
  return map[tool] ?? tool;
}

export function formatVector(vector: string): string {
  return vector
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
