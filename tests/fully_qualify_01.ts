namespace Foo.Bar {
  const $1: Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: Baz): Baz => "asdf" as Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Baz.Quux>()
  // Baz baz baz
  /* Baz baz baz */
}
