namespace Foo.Bar.X {
  const $1: Foo.Bar.Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: Foo.Bar.Baz): Foo.Bar.Baz => "asdf" as Foo.Bar.Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<Foo.Bar.Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Quux.Baz.Quux>()
  export class Clz extends Foo.Bar.Baz {
    // ...
  }
  export class Clz implements Foo.Bar.Baz {
    // ...
  }
  export interface Clz extends Foo.Bar.Baz {
    // ...
  }
  interface Clz extends Foo.Bar.Baz<string> {
    // ...
  }
  export class Baz {
    // ...
  }
  function foo(message: string) {
    throw new Error(Foo.Bar.Baz(message));
  }
  function foo(character: string) {
    switch (character) {
      case Foo.Bar.Baz.Plus:
      case Foo.Bar.Baz.Minus:
        return true;
      default:
        return Foo.Bar.Baz;
    }
  }
  function Baz() { }
  function Baz<T>() { }
  namespace Baz { }
  type Baz = { }
  type Baz: Quux = { }
  Foo.Bar.Baz { } // Even though this is illegal
  var foo = { Baz: "foo" };
  // Baz baz baz
  /* Baz baz baz */
}
