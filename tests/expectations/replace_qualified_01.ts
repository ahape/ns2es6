import { Baz as FBs_$_Baz } from "./baz";

namespace Foo.Bar.X {
  const $1: FBs_$_Baz = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: FBs_$_Baz): FBs_$_Baz => "asdf" as FBs_$_Baz;
  const $4 = (Baz?: number): void => { "asdf" }
  const _1 = this.fn<FBs_$_Baz>()
  const _2 = this.fn<Bazz>()
  const _3 = this.fn<Baz.Quux>()
  export class Clz extends FBs_$_Baz {
    // ...
  }
  export class Clz implements FBs_$_Baz {
    // ...
  }
  export class Baz {
    // ...
  }
  // Baz baz baz
  /* Baz baz baz */
}
