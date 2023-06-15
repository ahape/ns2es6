import { Baz } from "./baz";
const FBBs_$_Bam = Baz.Bam;
const FBBs_$_Bing = Baz.Bing;
namespace Foo.Bar.X {
  const $1: FBBs_$_Bing = "asdf";
  const $2 = this.Baz;
  const $3 = (Baz: FBBs_$_Bam): FBBs_$_Bam => "asdf" as FBBs_$_Bam;
}
