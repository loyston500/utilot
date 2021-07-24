pub enum Op {
    Pipe,
    File,
    FileOut,
    FileErr,
    Coln,
}

pub enum Instrs {
    Pipe,
    File,
    FileOut,
    FileErr,
    Coln,
}

#[derive(Debug)]
pub enum Token {
    PartialOp(String),
    Str(String),
}

#[derive(Debug)]
pub enum TokenizerError {
    StringScanEOF,
    EscapeSeqEOF,
    PatScanEOF,
    PatZeroLength,
}

pub fn tokenize(chars: Vec<char>) -> Result<Vec<Token>, TokenizerError> {
    let mut i = 0;
    let mut tokens: Vec<Token> = Vec::new();
    let mut temp: Vec<char> = Vec::new();

    while i < chars.len() {
        match chars[i] {
            '\\' => {
                i += 1;
                if !(i < chars.len()) {
                    return Err(TokenizerError::EscapeSeqEOF);
                }
                
                if chars[i] == 'n' {
                    temp.push('\n');
                } else {
                    temp.push(chars[i]);
                }
            }

            '>' | '|' | ';' => {
                let mut s = temp.iter().collect::<String>();

                // this is to support 1> and 2>
                // all other pairs will be considered as seperate tokens
                if (chars[i] == '>'/*|| chars[i] == '|'*/) && (s == "1" || s == "2") {
                    tokens.push(Token::PartialOp(format!("{}{}", s, chars[i]).to_string()));
                } else {
                    if s.len() != 0 {
                        tokens.push(Token::Str(s));
                    }
                    tokens.push(Token::PartialOp(chars[i].to_string()));
                }

                temp.clear();
            }

            ' ' | '\n' => {
                if temp.len() != 0 {
                    tokens.push(Token::Str(temp.iter().collect::<String>()));
                    temp.clear();
                }
            }

            '"' | '\'' => {
                let c = chars[i].clone();
                i += 1;
                if !(i < chars.len()) {
                    return Err(TokenizerError::StringScanEOF);
                }

                if chars[i] == c {
                    // basically if the string is '' or "" then
                    // keep the quotes too
                    temp.push(c.clone());
                    temp.push(c.clone());
                } else {
                    while chars[i] != c {
                        temp.push(chars[i].clone());
                        i += 1;

                        if !(i < chars.len()) {
                            return Err(TokenizerError::StringScanEOF);
                        }
                    }
                }
            }

            '*' => {
                // with this you can pass text with both quotes and newlines
                /* example:
                echo *EOF
                    print('hello')
                EOF

                also works with codeblocks:

                echo *```py
                    print('hello')
                ```
                */

                let mut pat = String::new();
                loop {
                    i += 1;
                    if !(i < chars.len()) {
                        return Err(TokenizerError::PatScanEOF);
                    }
                    match chars[i] {
                        'a'..='z' | 'A'..='Z' | '0'..='9' | '`' => {
                            pat.push(chars[i].clone());
                        }
                        _ => {
                            break;
                        }
                    }
                }

                if pat.len() == 0 {
                    return Err(TokenizerError::PatZeroLength);
                }

                pat = if pat.starts_with("```") {
                    "```".to_string()
                } else {
                    pat
                };

                let mut cont = String::new();
                while !cont.ends_with(&pat) {
                    match chars.get(i) {
                        Some(some) => cont.push(some.clone()),
                        None => return Err(TokenizerError::PatScanEOF),
                    }

                    i += 1;
                }
                i -= 1;

                let cont = cont.chars().collect::<Vec<char>>();
                temp.extend(&cont[..cont.len() - pat.len()]);
            }

            _ => {
                temp.push(chars[i].clone());
            }
        }
        i += 1;
    }

    if temp.len() != 0 {
        tokens.push(Token::Str(temp.iter().collect::<String>()));
    }

    return Ok(tokens);
}

/*fn main() {
    let mut chars = String::from(
r#"a > *EOF lol EOF"#).chars().collect::<Vec<char>>();

    dbg!(tokenize(chars));

}
*/
