let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      pkg-config
    ];

    buildInputs = with pkgs; [
      (pkgs.python311.withPackages (python-pkgs:
        with python-pkgs; [
          fastapi
        ]))
    ];

    shellHook = ''
      export PKG_CONFIG_PATH="${pkgs.pkg-config}/lib/pkgconfig"
    '';
  }
