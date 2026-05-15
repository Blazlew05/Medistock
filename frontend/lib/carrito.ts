import type { ItemCarrito, Producto } from "./api";

const KEY = "medistock_carrito";

export const carrito = {
  get(): ItemCarrito[] {
    if (typeof window === "undefined") return [];
    try {
      return JSON.parse(localStorage.getItem(KEY) || "[]");
    } catch {
      return [];
    }
  },
  set(items: ItemCarrito[]) {
    if (typeof window === "undefined") return;
    localStorage.setItem(KEY, JSON.stringify(items));
    window.dispatchEvent(new Event("carrito-actualizado"));
  },
  agregar(producto: Producto, cantidad: number = 1) {
    const items = this.get();
    const existente = items.find((i) => i.producto.codigo === producto.codigo);
    if (existente) {
      existente.cantidad += cantidad;
    } else {
      items.push({ producto, cantidad });
    }
    this.set(items);
  },
  quitar(codigo: string) {
    this.set(this.get().filter((i) => i.producto.codigo !== codigo));
  },
  cambiarCantidad(codigo: string, cantidad: number) {
    const items = this.get();
    const item = items.find((i) => i.producto.codigo === codigo);
    if (item) item.cantidad = Math.max(1, cantidad);
    this.set(items);
  },
  vaciar() {
    this.set([]);
  },
  total(): number {
    return this.get().reduce((acc, i) => acc + i.producto.precio * i.cantidad, 0);
  },
  cantidadItems(): number {
    return this.get().reduce((acc, i) => acc + i.cantidad, 0);
  },
};
