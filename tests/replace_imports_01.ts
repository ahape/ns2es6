namespace Something {
  import FBBs = Foo.Bar.Baz;
  import BBFs = Bar.Baz.Foo;
  import Hi = Aloha.Bonjour.Hola;

  function fn(s: BBFs.Type1): BBFs.Type2 {
    throw new FBBs.Error("Not implemented");
  }

  const something = new Hi.Type1<string>();
  // Hi there
  // import This.Is.A.Comment
  /*
  import something
  */
}
