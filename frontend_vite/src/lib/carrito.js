const KEY = "medistock_carrito";

export const carrito = {
  get() {
    if (typeof window === "undefined") return [];
    try {
      return JSON.parse(localStorage.getItem(KEY) || "[]");
    } catch {
      return [];
    }
  },
  set(items) {
    if (typeof window === "undefined") return;
    localStorage.setItem(KEY, JSON.stringify(items));
    window.dispatchEvent(new Event("carrito-actualizado"));
  },
  agregar(producto, cantidad = 1) {
    const items = this.get();
    const existente = items.find((i) => i.producto.codigo === producto.codigo);
    if (existente) {
      existente.cantidad += cantidad;
    } else {
      items.push({ producto, cantidad });
    }
    this.set(items);
  },
  quitar(codigo) {
    this.set(this.get().filter((i) => i.producto.codigo !== codigo));
  },
  cambiarCantidad(codigo, cantidad) {
    const items = this.get();
    const item = items.find((i) => i.producto.codigo === codigo);
    if (item) item.cantidad = Math.max(1, cantidad);
    this.set(items);
  },
  vaciar() {
    this.set([]);
  },
  total() {
    return this.get().reduce((acc, i) => acc + i.producto.precio * i.cantidad, 0);
  },
  cantidadItems() {
    return this.get().reduce((acc, i) => acc + i.cantidad, 0);
  },
};
