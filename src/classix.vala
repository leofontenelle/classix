// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2

// LEFT CURLY BRACKET UPPER HOOK: "\xE2\x8E\xA7"
// LEFT CURLY BRACKET MIDDLE PIECE: "\xE2\x8E\xA8"
// LEFT CURLY BRACKET LOWER HOOK: "\xE2\x8E\xA9"
// CURLY BRACKET EXTENSION: "\xE2\x8E\xAA"

// LEFT SQUARE BRACKET UPPER CORNER: "\xE2\x8E\xA1"
// LEFT SQUARE BRACKET EXTENSION: "\xE2\x8E\xA2"
// LEFT SQUARE BRACKET LOWER CORNER: "\xE2\x8E\xA3"

// RIGHT SQUARE BRACKET UPPER CORNER: "0xE2 0x8E 0xA4"
// RIGHT SQUARE BRACKET EXTENSION: 0xE2 0x8E 0xA5
// RIGHT SQUARE BRACKET LOWER CORNER: 0xE2 0x8E 0xA6

public class Classix : Object {
 
  Gtk.Window main_window;
  Gtk.TextBuffer notes_buffer;
  Gtk.TreeView search_treeview;
  Gtk.ListStore search_results;
  Gtk.ProgressBar search_progressbar;
  Gtk.Entry search_entry;
  Regex word_regex;
  Timer timer;
  
  File? bindir;
  Gee.TreeMap<string, int32> dic;
  FileInputStream inv_stream;
  FileInputStream dat_stream;
  CharsetConverter converter;
  Regex dat_regex;
  Regex combining_chars;
  
  public Classix() {
     
    this.bindir = this.get_bindir();
    
    File ui_file;
    try {
      ui_file = get_file("classix.ui");
    } catch (IOError e) {
      error ("%s\n", e.message);
    }
    var builder = new Gtk.Builder();
    try {
      builder.add_from_file(ui_file.get_path());
    } catch (Error e) {
      error ("%s\n", e.message);
    }
    
    builder.connect_signals(this);
    
    this.search_treeview = builder.get_object("search_treeview") as Gtk.TreeView;
    this.search_results = builder.get_object("search_results") as Gtk.ListStore;
    assert ((Gtk.ListStore) this.search_treeview.model == this.search_results);
    
    this.notes_buffer = ((Gtk.TextView) builder.get_object("notes_textview")).get_buffer();
    
    this.main_window = builder.get_object("main_window") as Gtk.Window;
    this.main_window.show_all();
    
    this.search_progressbar = builder.get_object("search_progressbar") as Gtk.ProgressBar;
    this.search_progressbar.hide();
    
    this.search_entry = builder.get_object("search_entry") as Gtk.Entry;
    
    
    File dic_file;
    try {
      dic_file = this.get_file("CID10N4A.DIC");
    } catch (IOError e) {
      error ("%s\n", e.message);
    }
    this.dic = new Gee.TreeMap<string, int> ();
    
    this.set_dic.begin(dic_file, (obj, res) => {
      this.set_dic.end(res);
      this.search_entry.secondary_icon_sensitive = true;
    });
    
    
    File inv_file;
    try {
      inv_file = this.get_file("CID10N4A.INV");
    } catch (IOError e) {
      error ("%s\n", e.message);
    }
    try {
      this.inv_stream = inv_file.read();
    } catch (Error e) {
      error ("%s\n", e.message);
    }
    
    File dat_file;
    try {
      dat_file = this.get_file("CID10N4A.DAT");
    } catch (IOError e) {
      error ("%s\n", e.message);
    }
    try {
      this.dat_stream = dat_file.read();
    } catch (Error e) {
      error ("%s\n", e.message);
    }
    
    try {
      this.converter = new CharsetConverter ("UTF-8", "WINDOWS-1252");
    } catch (Error e) {
      error ("%s\n", e.message);
    }
    
    string pattern;
    pattern = """^(?P<code>[A-Z][\d]{2}(\.[\d-])?[\x{2020}*]?)  """;
    pattern += """(?P<title>[^|]*)\|  """;
    pattern += """(?P<inclusion_notes>(\| [^|\\]*)*)?""";
    pattern += """(\\ (?P<exclusion_notes>[^|]*(\| [^|]*)*))?""";
    try {
      this.dat_regex = new Regex(pattern, RegexCompileFlags.OPTIMIZE);
    } catch (RegexError e) {
      error ("%s\n", e.message);
    }
    
    pattern  = """[\x{0300}-\x{036f}""";
    pattern += """\x{1dc0}-\x{1dff}""";
    pattern += """\x{20d0}-\x{20ff}""";
    pattern += """\x{fe20}-\x{fe2f}]""";
    try {
      this.combining_chars = new Regex(pattern, RegexCompileFlags.OPTIMIZE);
    } catch (RegexError e) {
      error ("%s\n", e.message);
    }
    
    try {
      this.word_regex = new Regex("""\W+""", RegexCompileFlags.OPTIMIZE);
    } catch (RegexError e) {
      error ("%s\n", e.message);
    }
    
    this.timer = new Timer();
  }
  
  int32 buffer_to_int32 (uint8[] buffer) {
    assert (buffer.length == 4);
    // Little endian.
    // https://bugzilla.gnome.org/show_bug.cgi?id=659781#c1
    return ((int32[]) buffer)[0];
  }
  
  File? get_bindir() {
    var proc_file = File.new_for_path("/proc/self/exe");
    FileInfo proc_info;
    try {
      proc_info = proc_file.query_info("standard::symlink-target", FileQueryInfoFlags.NONE);
    } catch (Error e) {
      return null;
    }
    var self_path = proc_info.get_symlink_target();
    var self_file = File.new_for_path(self_path);
    if (self_file.query_exists()) {
      return self_file.get_parent();
    } else {
      return null;
    }
  }
  
  public File get_file(string filename) throws IOError {
  
    File file;
  
    if (this.bindir == null) {
      // "assignment from incompatible pointer type"
      foreach (string? dir in Environment.get_system_data_dirs()) {
        file = File.new_for_path(dir).get_child("classix").get_child(filename);
        if (file.query_exists()) return file;
      }
    
      file = File.new_for_path(Environment.get_current_dir()).get_child(filename);
      if (file.query_exists()) return file;
    
      throw new IOError.NOT_FOUND("Couldn't find file %s\n", filename);
    }
  
    file = this.bindir.get_child(filename);
    if (file.query_exists()) return file;
  
    switch (this.bindir.get_basename()) {
    case "src":
      // We are in the source code tree
      file = this.bindir.get_parent().get_child("data").get_child(filename);
      if (file.query_exists()) return file;
      break;
    case "bin":
      file = this.bindir.get_parent().get_child("share").get_child("classix").get_child(filename);
      if (file.query_exists()) return file;
      break;
    }
  
    throw new IOError.NOT_FOUND("Couldn't find file %s\n", filename);
  }
  
  async Gee.TreeSet<int32> get_matches(string[] words) {
    
    var wordsset = new Gee.HashSet<string>();
    foreach (string w in words) {
      wordsset.add(w);
    }
    
    string token;
    int32 inv_index, dat_index, count;
    var tokens = new Gee.HashMap<string, Gee.TreeSet<int32>>();
    
    // The longest list will have 6334 integers, plus the integer with the count.
    // Each integer is 4 bytes.
    var buffer = new uint8[25340];
    
    foreach  (string word in wordsset) {
      token = this.normalize(word);
      foreach (string dic_key in this.dic.keys) {
        // TODO: allow search to be interrupted.
        if (token in dic_key) {
          inv_index = this.dic[dic_key];
          try {
            this.inv_stream.seek(inv_index, SeekType.SET);
          } catch (Error e1) {
            error ("%s\n", e1.message);
          }
          try {
            yield this.inv_stream.read_async(buffer);
          } catch (IOError e2) {
            error ("%s\n", e2.message);
          }
          count = buffer_to_int32(buffer[0:4]);
          for (int32 i = 4; i <= count * 4; i += 4) {
            dat_index = buffer_to_int32(buffer[i:i+4]);
            if (tokens.has_key(token)) {
              tokens[token].add(dat_index);
            } else {
              tokens[token] = new Gee.TreeSet<int32>();
              tokens[token].add(dat_index);
            }
          }
        }
      }
    }
    
    var result = new Gee.TreeSet<int32>();
    bool first_pass = true;
    
    foreach (string new_key in tokens.keys) {
      // TODO: allow search to be interrupted.
      if (first_pass) {
        result = tokens[new_key];
        first_pass = false;
      } else {
        result.retain_all(tokens[new_key]);
      }
    }
    
    return result;
  }
  
  public async void get_node(int32 index,
                             out string code,
                             out string title, 
                             out string inclusion_notes,
                             out string exclusion_notes) {
    
    // The longest line has 1971 characters, excluding the EOL characters.
    uint8[] cp1252_buffer = new uint8[2048];
    // Converted to UTF-8, the longest line has 2039 bytes, without EOL
    uint8[] utf8_buffer = new uint8[2048];
    
    try {
      this.dat_stream.seek(index, SeekType.SET);
    } catch (Error e1) {
      error ("%s\n", e1.message);
    }
    
    try {
      yield this.dat_stream.read_async(cp1252_buffer);
    } catch (Error e2) {
      error ("%s\n", e2.message);
    }
    
    for (int i = 0; i < cp1252_buffer.length; i++) {
      if (cp1252_buffer[i] == (uint8) '\r') {
        cp1252_buffer = cp1252_buffer[0:i];
        break;
      }
    }
    
    
    try {
      size_t bytes_read, bytes_written;
      this.converter.convert(cp1252_buffer,
                             utf8_buffer,
                             ConverterFlags.NO_FLAGS,
                             out bytes_read,
                             out bytes_written);
    } catch (Error e3) {
      error ("%s\n", e3.message);
    }
    
    MatchInfo match;
    this.dat_regex.match((string) utf8_buffer, 0, out match);
    
    code = match.fetch_named("code");
    title = match.fetch_named("title");
    
    string tmp;
    tmp = match.fetch_named("inclusion_notes") ?? "";
    inclusion_notes = (tmp != "") ? tmp.substring(2).replace("| ", "\n") : "";

    // Right square bracket upper corner
    inclusion_notes = inclusion_notes.replace("@<@", "\xE2\x8E\xA4");
    // Right square bracket extension
    inclusion_notes = inclusion_notes.replace("@#@", "\xE2\x8E\xA5");
    // Right square bracket lower corner
    inclusion_notes = inclusion_notes.replace("@>@", "\xE2\x8E\xA6");
    
    tmp = match.fetch_named("exclusion_notes") ?? "";
    exclusion_notes = (tmp != "") ? tmp.replace("| ", "\n") : "";

    // Right square bracket upper corner
    exclusion_notes = exclusion_notes.replace("@<@", "\xE2\x8E\xA4");
    // Right square bracket extension
    exclusion_notes = exclusion_notes.replace("@#@", "\xE2\x8E\xA5");
    // Right square bracket lower corner
    exclusion_notes = exclusion_notes.replace("@>@", "\xE2\x8E\xA6");

  }
  
  string normalize (string str) {
    string result = str.up().normalize(-1, NormalizeMode.NFD);
    try {
      result = this.combining_chars.replace_literal(result, result.length, 0, "");
    } catch (RegexError e) {
      error ("%s\n", e.message);
    }
    return result;
  }
  
  [CCode (instance_pos = -1)]
  public void on_main_window_destroy (Gtk.Window window) {
    Gtk.main_quit();
  }
  
  [CCode (instance_pos = -1)]
  public void on_search_entry_activate (Gtk.Entry entry) {
    
    this.timer.start();
    this.search_entry.secondary_icon_sensitive = false;
    
    this.search_progressbar.show();
    this.search_treeview.set_model(null);
    this.search_results.clear();
    
    string entry_text = entry.get_text();
    stdout.printf("Searching for: %s\n", entry_text);
    string[] words = this.word_regex.split(entry_text);
    this.search.begin(words, (obj, res) => {
      this.search.end(res);
      this.search_treeview.set_model(this.search_results);
      this.search_progressbar.hide();
      this.search_progressbar.set_fraction(0.0);
      this.timer.stop();
      stdout.printf("%fs elapsed\n", this.timer.elapsed());
      this.search_entry.secondary_icon_sensitive = true;
    });
  }
  
  [CCode (instance_pos = -1)]
  public void on_search_selection_changed(Gtk.TreeSelection selection) {
    
    assert (selection.get_mode() == Gtk.SelectionMode.SINGLE);
    
    Gtk.TreeModel model;
    Gtk.TreeIter iter;
    
    if ( !selection.get_selected(out model, out iter)) {
      this.notes_buffer.set_text("");
      return;
    }
    assert (model == (Gtk.TreeModel) this.search_results);

    Value inclusion_notes, exclusion_notes;
    model.get_value(iter, 2, out inclusion_notes);
    model.get_value(iter, 3, out exclusion_notes);
    string text;
    text = (string) inclusion_notes;
    if ((string) exclusion_notes != "") {
      if (text != "") text += "\n\n";
      text += "Exclui:\n" + (string) exclusion_notes;
    }
    
    this.notes_buffer.set_text(text);
  }
  
  public void run () {
  
    Gtk.main();
    
  }
  
  public async void search (string[] words) {
    
    Gee.TreeSet<int32> matches = yield get_matches (words);
    
    string code, title, inclusion_notes, exclusion_notes;
    Gtk.TreeIter iter;
    double fraction = 0.0;
    double increment = 1.0 / matches.size;
    
    foreach (int32 match in matches) {
      yield get_node(match, out code, out title, out inclusion_notes, out exclusion_notes);
      this.search_results.append(out iter);
      this.search_results.set(iter, 0, code, 1, title, 2, inclusion_notes, 3, exclusion_notes);
      fraction += increment;
      this.search_progressbar.set_fraction(fraction);
    }
  }
  
  async void set_dic (File dic_file) {
    
    DataInputStream dic_stream;
    try {
      dic_stream = new DataInputStream (dic_file.read());
      dic_stream.newline_type = DataStreamNewlineType.CR_LF;
    } catch (Error e1) {
      error ("%s\n", e1.message);
    }
    
    string? line;
    //size_t length;
    string[] key_n_value;
    try {
      line = yield dic_stream.read_line_async ();
      while ((line = yield dic_stream.read_line_async ()) != null) {
        key_n_value = line.split(",", 2);
        this.dic[key_n_value[0]] =  int.parse(key_n_value[1]);
      }
    } catch (Error e2) {
      error ("%s\n", e2.message);
    }
  }
}


int main (string[] argv) {
  Gtk.init(ref argv);
  var classix = new Classix();
  classix.run();
  return 0;
}
