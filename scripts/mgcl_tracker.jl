using ArgParse
using Pandas

# THIS FILE IS NOT INTENDED FOR USE! 
# I am trying to learn Julia by converting my latest script.

# there are no classes in Julia... so this will be interesting

function parse_commandline()
    s = ArgParseSettings()

    add_arg_group!(s, "Mutually exclusive options", exclusive = true, required = true)
    @add_arg_table! s begin
        "--range", "-r"
        nargs = 2
        help = "The lower and upper bound MGCL numbers, from LOWER to UPPER (inclusive)"
        metavar = ["LOWER", "UPPER"]

        "--file", "-f"
        help = "A CSV/XLSX of MGCL Numbers to search for"
    end

    add_arg_group!(s, "Required arguments", required = true)
    @add_arg_table s begin
        "--start_dir", "-d"
        help = "path to the starting directory"
        required = true
        "--exts", "-e"
        help = "The upper bound MGCL number to include in count (default is png jpg jpeg)"
        default = ["png", "jpg", "jpeg"]
        required = false
    end

    return parse_args(s)
end

function main()
    parsed_args = parse_commandline()
    println("Parsed args:")
    for (arg, val) in parsed_args
        println("  $arg  =>  $val")
    end
end

main()