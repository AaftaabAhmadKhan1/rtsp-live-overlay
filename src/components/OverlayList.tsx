import type { OverlayItem } from "./OverlayCanvas";

type Props = {
  items: OverlayItem[];
  onAddText: () => void;
  onAddImage: (file: File) => void;
  onRemove: (id: string) => void;
  onChangeText: (id: string, text: string) => void;
};

export default function OverlayList({ items, onAddText, onAddImage, onRemove, onChangeText }: Props) {
  return (
    <div className="list">
      <div className="row">
        <button className="btn" onClick={onAddText}>+ Text</button>
        <label className="btn">
          + Logo
          <input type="file" accept="image/*" style={{display:"none"}}
            onChange={e => e.target.files?.[0] && onAddImage(e.target.files[0])} />
        </label>
      </div>
      <ul>
        {items.map(it => (
          <li key={it.id} style={{display:"flex", gap:8, alignItems:"center", marginTop:6}}>
            <code>#{it.id.slice(0,6)}</code>
            {it.type === "text" ? (
              <input value={it.content} onChange={e => onChangeText(it.id, e.target.value)} />
            ) : <span>image</span>}
            <button className="btn" onClick={() => onRemove(it.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
