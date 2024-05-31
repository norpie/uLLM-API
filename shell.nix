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
          pip
        ]))
    ];

    shellHook = ''
      export PKG_CONFIG_PATH="${pkgs.pkg-config}/lib/pkgconfig"
      export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/"
      python -m venv .venv
      source .venv/bin/activate
    '';
  }
