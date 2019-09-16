from tritki.markdown import convert

if __name__ == "__main__":
    text = """\
# Heading

This is content.  Its a lot of content, and I will continue to type for
as long as I possibly can stand it, just spewing out random gibberish so
that I have a corpus of something to test.

There will be some **bold** text, and some italian or is that *italic*
text?  That has never made sense to me.  The text face catagory for normal
text is **[[Rome|Roman]]**, but the subtype for slanted text is "*[[Italic]]*", even though
Rome was an Italic tribe, not the other way around.

(tm) (r) (c) Tritium - 1st 1/4 the time
"""

    html = convert(text)

    print(html)