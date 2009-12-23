# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

LANG=C
export LANG
PGUSER=postgres
export PGUSER

mesg n
