# name: UMU-Theme
# author: UMU

function fish_prompt --description 'Write out the prompt'
    set -l last_pipestatus $pipestatus
    set -l normal (set_color normal)

    # Color the prompt differently when we're root
    set -l color_prefix $fish_color_command
    set -l color_user $fish_color_param
    set -l color_cwd $fish_color_normal
    set -l color_time $fish_color_hg_modified
    set -l color_suffix $fish_color_error

    set -l prefix '# '
    set -l suffix '$ '
    if contains -- $USER root toor
        set suffix '> '
    end

    # If we're running via SSH, change the host color.
    set -l color_host $fish_color_cwd
    if set -q SSH_TTY
        set color_host $fish_color_host_remote
    end

    # Write pipestatus
    set -l prompt_status (__fish_print_pipestatus " C:" "" "|" (set_color $fish_color_status) (set_color --bold $fish_color_status) $last_pipestatus)

    echo -s -n \n (set_color $color_prefix) $prefix (set_color $color_user) "$USER" $normal " @ " (set_color $color_host) (prompt_hostname) $normal ' ' (pwd) (fish_vcs_prompt) " [" (set_color $color_time) (date +"%H:%M:%S") $normal "]" $prompt_status \n (set_color $color_suffix) $suffix
end
