namespace Foo.Bar.X {
  const $1: Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: Baz): Baz => "asdf" as Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Quux.Baz.Quux>()
  export class Clz extends Baz {
    // ...
  }
  export class Clz implements Baz {
    // ...
  }
  export interface Clz extends Baz {
    // ...
  }
  interface Clz extends Baz<string> {
    // ...
  }
  export class Baz {
    // ...
  }
  function foo(message: string) {
    throw new Error(Bar.Baz(message));
  }
  function foo(character: string) {
    switch (character) {
      case Bar.Baz.Plus:
      case Bar.Baz.Minus:
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
  Baz { } // Even though this is illegal
  var foo = { Baz: "foo" };
  // Baz baz baz
  /* Baz baz baz */
  interface IFoo extends Bar.Baz<string>
  {
      foo: XFoo<string>;
  }
}
