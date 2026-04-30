
fn main() {
    println!("cargo:rustc-link-search=native=/home/runner/.pyenv/versions/3.12.13/lib");
    println!("cargo:rustc-link-search=native=/home/jules/.pyenv/versions/3.12.13/lib");
    println!("cargo:rustc-link-lib=python3.12");
}
