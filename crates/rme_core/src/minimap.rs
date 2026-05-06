pub struct Minimap;

impl Minimap {
    pub fn new() -> Self {
        Self
    }

    pub fn pixels(&self) -> Vec<u8> {
        vec![]
    }
}

impl Default for Minimap {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::Minimap;

    #[test]
    fn test_buffer() {
        let b = Minimap::new();
        assert_eq!(b.pixels().len(), 0);
    }
}
