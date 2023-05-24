namespace Foo.Bar.Baz {
  export class Baze { }
  export class Clazz extends Baze { }
  export abstract class Abz<T> {
    public readonly foo: T;
  }
  function butNotMe() {
    // ...
  }
}
function norMe() {
  // ...
}
 namespace Foo.Bar.Baz.Three.More.Levels {
  export const foo: string = "asdf";
  export let bar = () => 1
  export var baz: Record<string, number> = {};
}
namespace Foo.Bar.Baz.Three.More.Levels.Five.More.For.Good.Measure{
  // This is export within a comment
  // export within a comment
  /* export within a comment */
  //export class DontMindMe { }
  export interface IFoo {
    blah: string;
  }
  var export = 1;
  export type TFoo = number | string;
  export enum EFoo { One, Two, Export }
  export function funFoo() { }
  export namespace Last {
    export type Hi = string | number;
  }
}
