# Markdown Link Check

Gather URLs from multiple markdown files, perform address sanity checks and check the status code.

## Examples
Go to the root directory of the project, which you want to scan:

`md_link_check`
(Check every link and print invalid pages to stdout)

Search for specifc patterns:

`md_link_check --pattern www.github`
(Restrict the link list to links starting with "https://www.github")

Gather the links with unix tools:

`grep -rwohP '.' -e "\(https\:\/\/www.github\S*\)" > links.txt`

`md_link_check --input-file links.txt --output-file bad_links.txt`

## Further handling of the links

If you work with VIM you can replace the links with a few commands:  
(Within vim)

:%s/.*/grep -rl & '.' | xargs sed -i 's#&##g'
(Search for the link and list the file names where it was found, pipe those files into
 sed to replace the link with a new one, Enter the new link between the last two hashtags)

Execute replace commands:

:w !sh

### Author
Sebastian Fricke
2020
