namespace Foo.Bar.X {
  const $1: Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: Baz): Baz => "asdf" as Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Baz.Quux>()
  export class Clz extends Baz {
    // ...
  }
  export class Clz implements Baz {
    // ...
  }
  export class Baz {
    // ...
  }
  // Baz baz baz
  /* Baz baz baz */
}
