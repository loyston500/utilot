use std::collections::HashMap;

const CHAR_PREFIX: &str = "-";
const STR_PREFIX: &str = "--";

#[derive(Debug, Clone)]
pub struct ArgInfo {
    pub optional: bool,
    pub names: Vec<String>,
    pub id: String,
    pub def_value: Option<String>,
    pub greedy: bool,
}

impl ArgInfo {
    pub fn new(
        names: Vec<String>,
        id: String,
        def_value: Option<String>,
        greedy: bool,
        optional: bool,
    ) -> Self {
        return Self {
            names,
            id,
            def_value,
            greedy,
            optional,
        };
    }
}

#[derive(Debug, Clone)]
pub enum ParserError {
    Init(String),
    ValueNotFound(usize),
    ArgNotFound(usize),
}

pub fn parser(
    mut list: Vec<String>,
    arg_infos: Vec<ArgInfo>,
) -> Result<(HashMap<String, String>, Vec<String>), ParserError> {
    let mut params: HashMap<String, String> = HashMap::new();

    // initialization
    for (n, arg_info) in arg_infos.iter().enumerate() {
        if arg_info.names.len() != 2 {
            return Err(ParserError::Init("need exactly two names.".to_string()));
        }

        let (a, b) = (arg_info.names[0].clone(), arg_info.names[1].clone());

        if params.contains_key(&a) {
            return Err(ParserError::Init(
                "more than one instance of same argument is passed.".to_string(),
            ));
        }

        if a.len() != 1 || b.len() <= 1 {
            return Err(ParserError::Init(
                "name1 must be a single character and name2 must not be a single character."
                    .to_string(),
            ));
        }

        let mut i = 0;
        let mut count = 0;
        while i < list.len() {
            if (list[i].starts_with(STR_PREFIX) && b == list[i][STR_PREFIX.len()..]) {
                list.remove(i);

                let some = if arg_info.greedy {
                    if let Some(some) = list.get(i /*+ 1*/) {
                        let s = some.clone();
                        list.remove(i);
                        i += 1;
                        s
                    } else {
                        if let Some(value) = &arg_info.def_value {
                            value.clone()
                        } else {
                            return Err(ParserError::ValueNotFound(n));
                        }
                    }
                } else {
                    "".to_string()
                };

                params.insert(arg_info.id.clone(), some);

                count += 1;
            } else if (list[i].starts_with(CHAR_PREFIX) && list[i].contains(&a)) {
                list[i] = list[i].replace(&a, "");
                
                let some = if arg_info.greedy {
                    if let Some(some) = list.get(i + 1) {
                        let some = some.clone();
                        
                        if list[i] == CHAR_PREFIX {
                            list.remove(i);
                            list.remove(i);
                        }
                        
                        i += 1;
                        some
                    } else {
                        
                        if list[i] == CHAR_PREFIX {
                            list.remove(i);
                        }
                        
                        if let Some(value) = &arg_info.def_value {
                            value.clone()
                        } else {
                            return Err(ParserError::ValueNotFound(n));
                        }
                    }
                } else {
                    if list[i] == CHAR_PREFIX {
                            list.remove(i);
                    }
                    "".to_string()
                };

                params.insert(arg_info.id.clone(), some);

                count += 1;
            }

            i += 1;
        }

        if !arg_info.optional && count == 0 {
            return Err(ParserError::ArgNotFound(n));
        }
    }

    return Ok((params, list));
}

/*argparser(
    args,
    [
        argument(type="optional", names=["fucc", "f"]),
        argument(type="mandatory", greedy=True, names=["ascii_distros"])
    ]
)
*/
/*fn main() {
    let fucc = parser(vec!["-abc".to_string(), "lol".to_string(), "-lmfao".to_string()],
        vec![
            ArgInfo::new(vec!["g".to_string(), "abc".to_string()], None, true, false)
        ]
    );
    dbg!(fucc);
}*/
