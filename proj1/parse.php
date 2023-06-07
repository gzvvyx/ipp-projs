<?php

// parsovani argumentu

for ($i = 1; $i < $argc; $i++){
    // '--help' argument
    if ($argv[$i] == "--help" && $argc === 2){
            echo "Usage: php parse.php [--help]\n";
            echo "\n";
            echo "Script to filter out wrong .IPPCODE23 syntax.\n";
            echo "Reads input from standart input.\n";
            echo "\n";
            echo "  --help  Prints help.\n";
            exit(0);
    } else exit(10);
}

$input = array();
$temp = array();

$i = 0;
// odstraneni vsech nechtenych casti ippcode23 programu
while ($line = fgets(STDIN)){

    // odstraneni komentaru
    $temp = explode("#", $line, 255);
    $line = $temp[0];
    unset($temp);
    // rozdeleni radku na casti
    $temp = explode(" ", $line, 255);

    // odstraneni odradkovani z posledni casti radku
    $x = count($temp)-1;
    $temp[$x] = trim($temp[$x]);

    // odstraneni prazdnych casti radku
    for($j = $x; $j >= 0; $j--){
        if ($temp[$j] == ""){
            array_splice($temp, $j, 1);
        }
    }

    // ulozeni zpracovanych casti radku
    if (count($temp)){
        $input[$i++] = $temp;
    }
    unset($temp);
}

// (<element>, <attribute>, <type>, <value>, <order>)
// funkce pro vypsani XML reprezentace ippcode23 programu
function xml_write(string $elem, string $att, string $arg1, string $arg2, int $ord){
    global $xw;
    xmlwriter_start_element($xw, $elem);
    xmlwriter_start_attribute($xw, $att);
    if ($ord){
        xmlwriter_text($xw, $ord);
        xmlwriter_start_attribute($xw, $arg1);
        xmlwriter_text($xw, $arg2);
    } else {
        xmlwriter_text($xw, $arg1);
        if ($elem != "program"){
            xmlwriter_end_attribute($xw);
            xmlwriter_text($xw, $arg2);
            xmlwriter_end_element($xw);
        } else xmlwriter_end_attribute($xw);
    }
}

// zacatek XML
$xw = xmlwriter_open_memory();
xmlwriter_set_indent($xw, 1);
$res = xmlwriter_set_indent_string($xw, " ");
xmlwriter_start_document($xw, "1.0", "UTF-8");

// kontrola hlavicky
if (strtolower($input[0][0]) !== ".ippcode23"){
    exit(21);
}

xml_write("program", "language", "IPPcode23", "", 0);

// 2D pole instrukci a jejich dat
$commands = array(
    array("MOVE", 3, "S"),
    array("CREATEFRAME", 1),
    array("PUSHFRAME", 1),
    array("POPFRAME", 1),
    array("DEFVAR", 2, "V"),
    array("CALL", 2, "L"),
    array("RETURN", 1),
    array("PUSHS", 2, "S"),
    array("POPS", 2, "V"),
    array("ADD", 4),
    array("SUB", 4),
    array("MUL", 4),
    array("IDIV", 4),
    array("LT", 4),
    array("GT", 4),
    array("EQ", 4),
    array("AND", 4),
    array("OR", 4),
    array("NOT", 3, "S"),
    array("INT2CHAR", 3, "S"),
    array("STRI2INT", 4),
    array("READ", 3, "T"),
    array("WRITE", 2, "S"),
    array("CONCAT", 4),
    array("STRLEN", 3, "S"),
    array("GETCHAR", 4),
    array("SETCHAR", 4),
    array("TYPE", 3, "S"),
    array("LABEL", 2, "L"),
    array("JUMP", 2, "L"),
    array("JUMPIFEQ", 4),
    array("JUMPIFNEQ", 4),
    array("EXIT", 2, "S"),
    array("DPRINT", 2, "S"),
    array("BREAK", 1),
);
// 2. argument <ocekavana data>
// 4 -> <var><symb1><symb2>
// 3 -> <var><symb> || <var><type>
// 2 -> <var> || <symb> || <label>

// regularni vyraz pro <var>
function var_reg(string $str, string $num){
    if (preg_match("/^[TGL]F@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $str)){
        xml_write($num, "type", "var", $str, 0);
    } else exit(23);
}

// regularni vyraz pro <symb>
function symb_reg(string $str, string $num){
    $temp = explode("@", $str, 255);

    if ($temp[0] == "string"){
        for ($k = 2; $k < count($temp); $k++){
            $temp[1] = $temp[1] . "@" . $temp[$k];
        }
    } else if (count($temp) != 2){
        exit(23);
    }


    if ($temp[0] == "string" || $temp[0] == "bool" || $temp[0] == "int" || $temp[0] == "nil"){
        xml_write($num, "type", $temp[0], $temp[1], 0);
    } else if ($temp[0] == "GF" || $temp[0] == "TF" || $temp[0] == "LF"){
        // <symb> muze byt take <var>
        var_reg($str, $num);
    } else exit(23);

    if ($temp[0] == "string"){
        if (preg_match("/^((\\\\[0-9]{3})|[^\s\\\\])*$/", $temp[1])){

        } else exit(23);
    }
    if ($temp[0] == "bool"){
        if ($temp[1] == "true" || $temp[1] == "false"){

        } else exit(23);
    }
    if ($temp[0] == "int"){
        if (preg_match("/^[+-]?((([1-9][0-9]*(_[0-9]+)*)|0)|(0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*)|(0[oO]?[0-7]+(_[0-7]+)*))$/", $temp[1])){

        } else exit(23);
    }
    if ($temp[0] == "nil"){
        if ($temp[1] == "nil"){

        } else exit(23);
    }
}

// regularni vyraz pro <label>
function label_reg(string $str){
    if (preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $str)){
        xml_write("arg1", "type", "label", $str, 0);
    } else exit(23);
}

// regularni vyraz pro <type>
function type_reg(string $str){
    // string, bool, null, int
    if ($str == "string" || $str == "bool" || $str == "int"){
        xml_write("arg2", "type", "type", $str, 0);
    } else exit(23);
}

$found = false;
for ($i = 1; $i < count($input); $i++){
    foreach($commands as $c){
        if ($c[0] == strtoupper($input[$i][0])){
            if (count($input[$i]) != $c[1]){
                // spatny pocet argumentu
                exit(23);
            }
            $found = true;

            xml_write("instruction", "order", "opcode", $c[0], $i);

            // <var> || <symb> || <label>
            if ($c[1] === 2){
                if ($c[2] == "V"){
                    var_reg($input[$i][1], "arg1");
                }
                if ($c[2] == "S"){
                    symb_reg($input[$i][1], "arg1");
                }
                if ($c[2] == "L"){
                    label_reg($input[$i][1]);
                }
            }
            // <var><symb> || <var><type>
            if ($c[1] === 3){
                var_reg($input[$i][1], "arg1");

                if ($c[2] == "S"){
                    symb_reg($input[$i][2], "arg2");
                }
                if ($c[2] == "T"){
                    type_reg($input[$i][2]);
                }
            }
            // <var><symb1><symb2>
            if ($c[1] === 4){
                if ($c[0] == "JUMPIFEQ" || $c[0] == "JUMPIFNEQ"){
                    label_reg($input[$i][1]);
                } else var_reg($input[$i][1], "arg1");
                symb_reg($input[$i][2], "arg2");
                symb_reg($input[$i][3], "arg3");
            }

        }
    }
    xmlwriter_end_element($xw);
    // kontrola znamych prikazu
    if (!$found){
        exit(22);
    }
}

xmlwriter_end_element($xw); // end XML
echo xmlwriter_output_memory($xw); // print XML