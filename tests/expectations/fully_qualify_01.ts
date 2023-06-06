namespace Foo.Bar {
  const $1: Foo.Bar.Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: Foo.Bar.Baz): Foo.Bar.Baz => "asdf" as Foo.Bar.Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<Foo.Bar.Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Baz.Quux>()
  // Baz baz baz
  /* Baz baz baz */
}
