import { Rnd } from "react-rnd";

export type OverlayItem = {
  id: string;
  type: "text" | "image";
  content: string;
  x: number; y: number; width: number; height: number;
  rotation?: number; opacity?: number; zIndex?: number;
  style?: Record<string,string>;
};

type Props = {
  items: OverlayItem[];
  editing: boolean;
  onChange: (items: OverlayItem[]) => void;
};

export default function OverlayCanvas({ items, editing, onChange }: Props) {
  // container is position:relative; video below fills width
  const onDragResize = (id: string, px: {x:number,y:number,w:number,h:number}, parent: HTMLDivElement) => {
    const rect = parent.getBoundingClientRect();
    const nx = Math.min(Math.max(px.x / rect.width, 0), 1);
    const ny = Math.min(Math.max(px.y / rect.height, 0), 1);
    const nw = Math.min(Math.max(px.w / rect.width, 0), 1);
    const nh = Math.min(Math.max(px.h / rect.height, 0), 1);
    const next = items.map(it => it.id === id ? { ...it, x:nx, y:ny, width:nw, height:nh } : it);
    onChange(next);
  };

  return (
    <div className="overlay-container" id="overlay-parent" style={{ position:"relative" }}>
      {/* This component should be placed ABOVE the video via CSS stacking context */}
      {items.map(it => (
        <Rnd
          key={it.id}
          enableResizing={editing}
          disableDragging={!editing}
          bounds="parent"
          size={{ width: `calc(${it.width*100}% )`, height:`calc(${it.height*100}% )` }}
          position={{ x: 0, y: 0 }}
          style={{
            position:"absolute",
            left: `${it.x*100}%`,
            top: `${it.y*100}%`,
            transform: `translate(0,0) rotate(${it.rotation||0}deg)`,
            opacity: it.opacity ?? 1,
            zIndex: it.zIndex ?? 0,
            pointerEvents: editing ? "auto" : "none"
          }}
          onDragStop={(e,d) => {
            const parent = (document.getElementById("overlay-parent") as HTMLDivElement)!;
            onDragResize(it.id, { x: d.x, y: d.y, w: parent.clientWidth*it.width, h: parent.clientHeight*it.height }, parent);
          }}
          onResizeStop={(e,dir,ref,delta,pos) => {
            const parent = (document.getElementById("overlay-parent") as HTMLDivElement)!;
            onDragResize(it.id, { x: pos.x, y: pos.y, w: ref.offsetWidth, h: ref.offsetHeight }, parent);
          }}
        >
          {it.type === "text" ? (
            <div style={{
              width:"100%", height:"100%", display:"flex", alignItems:"center", justifyContent:"center",
              color: it.style?.color || "#fff",
              fontSize: it.style?.fontSize || "18px",
              fontWeight: it.style?.fontWeight || "700",
              textShadow: "0 1px 2px rgba(0,0,0,0.6)"
            }}>{it.content}</div>
          ) : (
            <img src={it.content} alt="logo" style={{ width:"100%", height:"100%", objectFit:"contain" }} />
          )}
        </Rnd>
      ))}
    </div>
  );
}
